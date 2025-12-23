"""
Hotel Cancellation Risk Tool - Ultimate Batch Processor
Combines the best of xlwings (run while Excel open) with robust batch processing
- Processes ALL CSV files in incoming folder
- Exports scored results to timestamped CSVs
- Archives processed files automatically
- Works while Excel is open
"""

import pandas as pd
import xlwings as xw
import os
import glob
import shutil
from datetime import datetime
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

# Base path
BASE_PATH = "/Users/eoghankealy/Documents/data_projects/hotel_bookings/risk_tool"

# File and folder paths
EXCEL_PATH = os.path.join(BASE_PATH, "cancellation_risk_tool.xlsm")
INCOMING_FOLDER = os.path.join(BASE_PATH, "incoming_bookings")
PROCESSED_FOLDER = os.path.join(BASE_PATH, "processed_bookings")
SCORED_OUTPUT_FOLDER = os.path.join(BASE_PATH, "scored_output")

SHEET_NAME = "cancellation_risk_tool"

REQUIRED_COLUMNS = [
    "lead_time",
    "country",
    "is_repeated_guest",
    "market_segment",
    "previous_cancellations",
    "booking_changes",
    "deposit_type",
    "adr",
    "total_of_special_requests"
]

START_ROW = 4  # First data row (row 3 is headers)
MAX_ROWS = 50000  # Maximum rows to scan for safety

# ============================================================================
# FOLDER MANAGEMENT
# ============================================================================

def ensure_folders_exist():
    """Create necessary folders if they don't exist"""
    folders = [INCOMING_FOLDER, PROCESSED_FOLDER, SCORED_OUTPUT_FOLDER]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✓ Created folder: {os.path.basename(folder)}/")

def find_csv_files():
    """Find all CSV files in the incoming folder"""
    csv_pattern = os.path.join(INCOMING_FOLDER, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    # Filter out files in subdirectories
    csv_files = [f for f in csv_files if os.path.dirname(f) == INCOMING_FOLDER]
    
    return sorted(csv_files)

def move_to_processed(csv_path):
    """Move processed CSV to the processed_bookings folder with timestamp"""
    filename = os.path.basename(csv_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{timestamp}_{filename}"
    destination = os.path.join(PROCESSED_FOLDER, new_filename)
    
    try:
        shutil.move(csv_path, destination)
        print(f"  ✓ Archived as: {new_filename}")
        return True
    except Exception as e:
        print(f"  ⚠️  Could not archive file: {e}")
        return False

# ============================================================================
# CSV PROCESSING
# ============================================================================

def load_and_validate_csv(csv_path):
    """Load CSV and validate required columns"""
    try:
        df = pd.read_csv(csv_path)
        
        # Case-insensitive column matching
        csv_cols_lower = {col.lower().strip(): col for col in df.columns}
        
        # Find required columns
        found_columns = {}
        missing_columns = []
        
        for req_col in REQUIRED_COLUMNS:
            req_col_lower = req_col.lower()
            
            if req_col_lower in csv_cols_lower:
                found_columns[req_col] = csv_cols_lower[req_col_lower]
            else:
                # Try fuzzy match
                found = False
                for csv_col_lower, csv_col_actual in csv_cols_lower.items():
                    if req_col_lower in csv_col_lower or csv_col_lower in req_col_lower:
                        found_columns[req_col] = csv_col_actual
                        found = True
                        break
                
                if not found:
                    missing_columns.append(req_col)
        
        if missing_columns:
            print(f"  ✗ Missing columns: {', '.join(missing_columns)}")
            return None
        
        # Extract and reorder columns
        df_clean = df[[found_columns[col] for col in REQUIRED_COLUMNS]].copy()
        df_clean.columns = REQUIRED_COLUMNS
        
        print(f"  ✓ Loaded {len(df_clean)} bookings")
        return df_clean
        
    except Exception as e:
        print(f"  ✗ Error reading CSV: {e}")
        return None

# ============================================================================
# EXCEL OPERATIONS (xlwings)
# ============================================================================

def open_excel_safely(excel_path, sheet_name):
    """
    Safely open Excel workbook and return sheet
    Works with Excel already open or closed
    """
    try:
        # Get or create Excel app instance
        app = xw.apps.active
        if not app:
            app = xw.App(visible=True)
        
        # Check if workbook already open by name (more reliable)
        wb = None
        excel_filename = os.path.basename(excel_path)
        
        for book in app.books:
            if book.name == excel_filename:
                wb = book
                print(f"  ✓ Using already-open workbook")
                break
        
        # Open if not already open
        if not wb:
            print(f"  • Opening workbook...")
            wb = app.books.open(excel_path)
            time.sleep(1)  # Give Excel time to load
        
        # Verify sheet exists
        sheet_names = [s.name for s in wb.sheets]
        if sheet_name not in sheet_names:
            raise ValueError(
                f"Sheet '{sheet_name}' not found. "
                f"Available sheets: {', '.join(sheet_names)}"
            )
        
        sheet = wb.sheets[sheet_name]
        return wb, sheet, app
        
    except Exception as e:
        print(f"  ✗ Error opening Excel: {e}")
        return None, None, None

def clear_data_range(sheet, start_row):
    """
    Clear only input columns (A:I), preserve formulas in K:L
    Safely determines last used row
    """
    try:
        # Read column A to find last used row
        col_a_values = sheet.range(f"A{start_row}:A{MAX_ROWS}").value
        
        last_row = start_row - 1
        if isinstance(col_a_values, list):
            for i, val in enumerate(col_a_values, start=start_row):
                if val not in (None, ""):
                    last_row = i
        
        # Clear input columns only (A:I)
        if last_row >= start_row:
            sheet.range(f"A{start_row}:I{last_row}").clear_contents()
            print(f"  ✓ Cleared rows {start_row} to {last_row}")
        else:
            print(f"  • No existing data to clear")
            
    except Exception as e:
        print(f"  ⚠️  Could not clear data: {e}")

def write_and_score_bookings(sheet, df, start_row):
    """
    Write booking data to Excel and read back calculated risk scores
    """
    try:
        # Write input data to columns A:I
        sheet.range(f"A{start_row}").value = df.values
        print(f"  ✓ Wrote {len(df)} bookings to Excel")
        
        # Give Excel time to calculate formulas
        time.sleep(2)
        
        # Read calculated results from columns K:L
        end_row = start_row + len(df) - 1
        results = sheet.range(f"K{start_row}:L{end_row}").value
        
        # Handle single row case
        if not isinstance(results[0], list):
            results = [results]
        
        # Create results DataFrame
        results_df = pd.DataFrame(
            results,
            columns=["Cancellation_Risk", "Probability_of_Cancelling"]
        )
        
        # Combine input and results
        final_df = pd.concat([df.reset_index(drop=True), results_df], axis=1)
        
        print(f"  ✓ Read calculated risk scores")
        return final_df
        
    except Exception as e:
        print(f"  ✗ Error writing/reading Excel: {e}")
        return None

# ============================================================================
# OUTPUT & REPORTING
# ============================================================================

def save_scored_csv(df, original_filename):
    """Save scored bookings to timestamped CSV in scored_output folder"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(original_filename)[0]
        output_filename = f"{base_name}_scored_{timestamp}.csv"
        output_path = os.path.join(SCORED_OUTPUT_FOLDER, output_filename)
        
        df.to_csv(output_path, index=False)
        print(f"  ✓ Saved scored results: {output_filename}")
        return output_path
        
    except Exception as e:
        print(f"  ✗ Error saving CSV: {e}")
        return None

def print_batch_summary(df, filename):
    """Print simple summary for a batch"""
    print(f"  ✓ Processed {len(df)} bookings from {filename}")

def print_final_summary(total_files, success_count, total_bookings):
    """Print final processing summary"""
    print("\n" + "="*60)
    print("📋 FINAL SUMMARY")
    print("="*60)
    print(f"CSV files found:        {total_files}")
    print(f"Successfully processed: {success_count}")
    print(f"Failed:                 {total_files - success_count}")
    print(f"Total bookings scored:  {total_bookings}")
    print("="*60)
    
    if success_count > 0:
        print(f"\n✓ Scored CSVs saved to: scored_output/")
        print(f"✓ Original CSVs archived in: processed_bookings/")
        print(f"✓ Excel file updated with latest batch")

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def process_single_csv(csv_path, wb, sheet):
    """Process a single CSV file through the risk tool"""
    filename = os.path.basename(csv_path)
    
    print(f"\n{'─'*60}")
    print(f"📄 Processing: {filename}")
    print(f"{'─'*60}")
    
    try:
        # Load and validate CSV
        df = load_and_validate_csv(csv_path)
        if df is None:
            return False, 0
        
        # Clear previous data in Excel
        clear_data_range(sheet, START_ROW)
        
        # Write data and read calculated scores
        scored_df = write_and_score_bookings(sheet, df, START_ROW)
        if scored_df is None:
            return False, 0
        
        # Save scored results to CSV
        output_path = save_scored_csv(scored_df, filename)
        if output_path is None:
            return False, 0
        
        # Print summary (wrapped in try-except to prevent summary errors from stopping processing)
        try:
            print_batch_summary(scored_df, filename)
        except Exception as e:
            print(f"  ⚠️  Could not print summary: {e}")
        
        # Archive original CSV (always do this, even if summary fails)
        move_to_processed(csv_path)
        
        return True, len(df)
        
    except Exception as e:
        print(f"  ✗ Error processing file: {e}")
        return False, 0

def main():
    """Main execution flow"""
    
    print("\n" + "="*60)
    print("🏨 HOTEL CANCELLATION RISK TOOL - ULTIMATE BATCH PROCESSOR")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # Ensure folders exist
    print("📁 Checking folders...")
    ensure_folders_exist()
    
    # Find CSV files
    print(f"\n🔍 Scanning: incoming_bookings/")
    csv_files = find_csv_files()
    
    if not csv_files:
        print("\n📭 No CSV files found in incoming_bookings folder")
        print(f"\n💡 Drop CSV files in: {INCOMING_FOLDER}")
        print("   Then run this script again\n")
        return
    
    print(f"✓ Found {len(csv_files)} CSV file(s):\n")
    for csv_file in csv_files:
        print(f"  • {os.path.basename(csv_file)}")
    
    # Open Excel workbook
    print(f"\n📂 Opening Excel workbook...")
    wb, sheet, app = open_excel_safely(EXCEL_PATH, SHEET_NAME)
    
    if wb is None:
        print("\n❌ Cannot proceed without Excel workbook\n")
        return
    
    print(f"✓ Excel opened successfully")
    print(f"✓ Using sheet: {SHEET_NAME}")
    
    # Process each CSV file
    success_count = 0
    total_bookings = 0
    
    for csv_path in csv_files:
        success, num_bookings = process_single_csv(csv_path, wb, sheet)
        if success:
            success_count += 1
            total_bookings += num_bookings
    
    # Final summary
    print_final_summary(len(csv_files), success_count, total_bookings)
    
    print(f"\n✅ Process completed!")
    print(f"⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n💡 Excel is still open - check the risk scores!\n")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user\n")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}\n")