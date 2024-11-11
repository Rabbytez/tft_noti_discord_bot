import json

def calculate_bench_value(bench_data, board_units,board_cost):
    bench_data= bench_data['bench_pieces']
    total_value = 0
    for piece in bench_data:

        champ_name= bench_data[piece]['name']
        if champ_name in board_cost:
            total_value += board_cost[champ_name]

    return total_value

def calculate_board_value(board_data):
    total_value = 0
    board_units = set()  # เก็บชื่อของตัวละครใน board
    board_cost = {}  # เก็บค่า cost ของแต่ละตัวละคร

    for piece in board_data:
        unit_name = piece.get("unit")
        cost = piece.get("cost", 0)
        tier = piece.get("tier", 1)
        piece_value = cost * tier
        total_value += piece_value

        # บันทึกชื่อของตัวละครและค่า cost ลงใน board_units และ board_cost
        board_units.add(unit_name)
        board_cost[unit_name] = cost

    return total_value, board_units, board_cost

def calculate_stage_score(stage_data, previous_board_value=0, previous_bench_value=0):
    # Extracting key info for each stage with default values if missing
    stage_round= stage_data['match_info']['round_type']['stage']

    stage_round = stage_round.split('-')[0]
    stage_round = int(stage_round)

    try:
        level= stage_data['me']['xp']['level']
    except:
        level= 0

    # print("Stage round:", stage_round)
    try:
        gold_str = stage_data["me"].get("gold", "0")  # Get gold as string, default to "0"
        gold = int(gold_str) if gold_str.isdigit() else 0  # Convert if non-empty, otherwise 0
        gold_earned = stage_data.get("gold_earned", 0)
        rerolls = stage_data.get("rerolls", 0)
    except KeyError:
        gold, gold_earned, rerolls = 0, 0, 0
    
    # คำนวณ board value โดยใช้ค่า board ก่อนหน้าในกรณีที่ไม่มีข้อมูล
    if len(stage_data['matchup_boards']['player_board']) > 0:
        board_value, board_units,board_cost = calculate_board_value(stage_data['matchup_boards']['player_board'])
        bench_value = calculate_bench_value(stage_data.get("bench", []), board_units,board_cost)
        total_value = board_value + bench_value        
    else:
        board_value = previous_board_value

        bench_value = previous_bench_value

        total_value = board_value + bench_value
    if board_value == 0:

        board_value = previous_board_value

        bench_value = previous_bench_value

        total_value = board_value + bench_value


    # print(board_value, bench_value, total_value)
    diff_board_value = total_value - previous_board_value

    gold_score = 100 if gold >=50 else 80 if gold >= 40 else 60 if gold >= 30 else 40 if gold >= 20 else 20 if gold >= 10 else 0

    reroll_cal= diff_board_value - (rerolls* 2)
    if reroll_cal < 0:
        reroll_score= 100+(reroll_cal*5)
    else:
        reroll_score= 100

    efficiency_score = min(100, 65 + (gold_earned + ((rerolls * 2)) + diff_board_value*3) )
    
    # Add board value impact
    if stage_round <= 2 or level <= 4:
        board_value_score = min(100, board_value * 8)
    elif stage_round <= 3 or level <= 6:
        board_value_score = min(100, board_value * 4)
    else:
        board_value_score = min(100, board_value * 3)  # Assuming a cap of 100 for board value effect
    
    # Weighted stage score including board value
    # print("Gold score:", gold_score)
    # print("Reroll score:", reroll_score)
    # print("Efficiency score:", efficiency_score)
    # print("Board value score:", board_value_score)
    # print(level)

    if stage_round == 1:
        board_value_score=100
    if stage_round <= 2:
        stage_score = (gold_score * 0.1) + (reroll_score * 0.2) + (efficiency_score * 0.2) + (board_value_score * 0.5)

    elif stage_round <= 5 or level <= 7:
        stage_score = (gold_score * 0.3) + (reroll_score * 0.25) + (efficiency_score * 0.15) + (board_value_score * 0.3)
    
    else:
        stage_score = (gold_score * 0.0) + (reroll_score * 0.4) + (efficiency_score * 0.2) + (board_value_score * 0.4)
    return stage_score, board_value

def calculate_final_rank(game_data):
    # Aggregate stage scores
    stage_scores = []
    previous_board_value = 0  # ตัวแปรสำหรับเก็บ board value ก่อนหน้า
    previous_bench_value = 0
    for stage_key in game_data:
        # print("Stage:", stage_key)
        stage_score, previous_board_value = calculate_stage_score(game_data[stage_key], previous_board_value, previous_bench_value)
        stage_scores.append(stage_score)
    
    # Calculate average score
    average_score = sum(stage_scores) / len(stage_scores) if stage_scores else 0
    # print("Stage scores:", stage_scores)


    if average_score >= 90:
        return 'SS'
    elif average_score >= 80:
        return 'S'
    elif average_score >= 70:
        return 'A'
    elif average_score >= 50:
        return 'B'
    else:
        return 'C'

with open('organized_stage_data.json') as f:
    game_data = json.load(f)

if __name__ == "__main__":
    # Example usage with multiple stages
    final_rank = calculate_final_rank(game_data)  # game_data contains all stages
    print(f"Final Econ Rate Rank: {final_rank}")
