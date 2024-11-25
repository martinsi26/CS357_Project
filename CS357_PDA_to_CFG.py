import csv
import json


def create_pda_json(states, input_alphabet, stack_alphabet, transitions, start_state, final_states):
    pda = {
        "states": states,
        "input_symbols": input_alphabet,
        "stack_symbols": stack_alphabet,
        "transitions": transitions,
        "initial_state": start_state,
        "final_states": final_states
    }
    return pda


def read_pda_from_csv(filename):
    states = []
    input_alphabet = []
    stack_alphabet = []
    transitions = {}
    start_state = None
    final_states = []

    with open(filename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip header row

        for row in csv_reader:
            component, *values = row

            if component == "states":
                states.extend(values)
            elif component == "input_alphabet":
                input_alphabet.extend(values)
            elif component == "stack_alphabet":
                stack_alphabet.extend(values)
            elif component == "transitions":
                current_state, input_symbol, popped_symbol, next_state, pushed_symbol = values
                # Initialize the list of transitions for the state
                if current_state not in transitions:
                    transitions[current_state] = []
                # Append a new transition as a dictionary
                transitions[current_state].append({
                    "input_symbol": input_symbol,
                    "popped_symbol": popped_symbol,
                    "next_state": next_state,
                    "pushed_symbol": pushed_symbol
                })
            elif component == "initial_state":
                start_state = values[0]
            elif component == "final_states":
                final_states.extend(values)

    # Return the dictionary directly from create_pda_json
    return create_pda_json(states, input_alphabet, stack_alphabet, transitions, start_state, final_states)


def validate_pda(pda_json):
    """
    Validates the structure and components of a PDA JSON object.
    """
    # Extract sets and validate them
    states = set(pda_json["states"])
    input_symbols = set(pda_json["input_symbols"])
    stack_symbols = set(pda_json["stack_symbols"])
    transitions = pda_json["transitions"]
    initial_state = pda_json["initial_state"]
    final_states = set(pda_json["final_states"])

    # Perform validations
    validate_non_empty_components(pda_json)
    validate_epsilon_usage(states, input_symbols, stack_symbols, initial_state, final_states)
    validate_no_overlap(states, input_symbols, stack_symbols)
    validate_initial_and_final_states(states, initial_state, final_states)
    validate_transitions(states, input_symbols, stack_symbols, transitions)
    validate_additional_constraints(pda_json, input_symbols, stack_symbols, states, final_states)

    print("PDA is valid.")


def validate_non_empty_components(pda_json):
    """
    Ensures that all required PDA components are non-empty.
    """
    if not pda_json["states"]:
        raise ValueError("States cannot be empty.")
    if not pda_json["input_symbols"]:
        raise ValueError("Input alphabet cannot be empty.")
    if not pda_json["stack_symbols"]:
        raise ValueError("Stack alphabet cannot be empty.")
    if not pda_json["transitions"]:
        raise ValueError("Transitions cannot be empty.")
    if pda_json["initial_state"] is None:
        raise ValueError("Initial state cannot be None.")
    if not pda_json["final_states"]:
        raise ValueError("Final states cannot be empty.")


def validate_epsilon_usage(states, input_symbols, stack_symbols, initial_state, final_states):
    """
    Ensures that 'epsilon' is not used improperly in the PDA.
    """
    if "epsilon" in states:
        raise ValueError("The empty string 'epsilon' cannot be used as a state.")
    if "epsilon" in input_symbols:
        raise ValueError("The empty string 'epsilon' cannot be used as an input symbol.")
    if "epsilon" in stack_symbols:
        raise ValueError("The empty string 'epsilon' cannot be used as a stack symbol.")
    if initial_state == "epsilon":
        raise ValueError("The empty string 'epsilon' cannot be used as the initial state.")
    if "epsilon" in final_states:
        raise ValueError("The empty string 'epsilon' cannot be used as a final state.")


def validate_no_overlap(states, input_symbols, stack_symbols):
    """
    Ensures that states do not overlap with input symbols or stack symbols.
    """
    overlapping = states & (input_symbols | stack_symbols)
    if overlapping:
        raise ValueError(f"States cannot overlap with input symbols or stack symbols: {', '.join(overlapping)}")


def validate_initial_and_final_states(states, initial_state, final_states):
    """
    Validates the existence of the initial state and all final states in the set of states.
    """
    if initial_state not in states:
        raise ValueError(f"Initial state '{initial_state}' is not a valid state.")
    for state in final_states:
        if state not in states:
            raise ValueError(f"Final state '{state}' is not a valid state.")


def validate_transitions(states, input_symbols, stack_symbols, transitions):
    """
    Ensures that all transitions use valid states, input symbols, and stack symbols.
    """
    for current_state, transitions_list in transitions.items():
        if current_state not in states:
            raise ValueError(f"Transition state '{current_state}' is not a valid state.")

        for transition in transitions_list:
            validate_transition(transition, current_state, states, input_symbols, stack_symbols)


def validate_transition(transition, current_state, states, input_symbols, stack_symbols):
    """
    Validates an individual transition entry.
    """
    input_symbol = transition["input_symbol"]
    popped_symbol = transition["popped_symbol"]
    next_state = transition["next_state"]
    pushed_symbol = transition["pushed_symbol"]

    if input_symbol != "epsilon" and input_symbol not in input_symbols:
        raise ValueError(f"Transition input symbol '{input_symbol}' is not a valid input symbol.")
    if popped_symbol != "epsilon" and popped_symbol not in stack_symbols:
        raise ValueError(f"Transition popped symbol '{popped_symbol}' is not a valid stack symbol.")
    if next_state not in states:
        raise ValueError(f"Transition next state '{next_state}' is not a valid state.")
    if pushed_symbol != "epsilon" and pushed_symbol not in stack_symbols:
        raise ValueError(f"Transition pushed symbol '{pushed_symbol}' is not a valid stack symbol.")


def validate_additional_constraints(pda_json, input_symbols, stack_symbols, states, final_states):
    """
    Ensures additional constraints are met for the PDA components.
    """
    initial_state = pda_json["initial_state"]
    if initial_state in input_symbols or initial_state in stack_symbols:
        raise ValueError(f"Initial state '{initial_state}' cannot be in input symbols or stack symbols.")

    for final_state in final_states:
        if final_state in input_symbols or final_state in stack_symbols:
            raise ValueError(f"Final state '{final_state}' cannot be in input symbols or stack symbols.")

    for input_symbol in input_symbols:
        if input_symbol in states:
            raise ValueError(f"Input symbol '{input_symbol}' cannot be a state.")

    for stack_symbol in stack_symbols:
        if stack_symbol in states:
            raise ValueError(f"Stack symbol '{stack_symbol}' cannot be a state.")


def validate_pda_conversion(pda_json):
    # Step 1: Check if there is only one final state
    if len(pda_json["final_states"]) > 1:
        error_message = "There are multiple final states"
        print(error_message)
        raise ValueError(f"PDA incorrect: {error_message}. Please update the PDA input.")

    # Step 2: Validate stack operations (pushes and pops)
    validate_stack_operations(pda_json)

    # Step 3: Check for transitions where the stack stays the same
    validate_stack_symbol_transitions(pda_json)

    # Print the updated PDA JSON for verification
    print("PDA is valid for conversion.")


def validate_stack_operations(pda_json):
    """
    Checks if the stack is properly emptied:
    - Tracks push and pop operations for each symbol.
    - Raises an error if any symbol is pushed more times than it is popped.
    """
    stack_operations = {}

    # Track all stack operations (pushes and pops)
    for current_state, transitions_list in pda_json["transitions"].items():
        for transition in transitions_list:
            # Track push operations
            if transition["pushed_symbol"] != "epsilon":  # If it's not epsilon, it's a push
                if transition["pushed_symbol"] not in stack_operations:
                    stack_operations[transition["pushed_symbol"]] = {'pushed': 0, 'popped': 0}
                stack_operations[transition["pushed_symbol"]]['pushed'] += 1
            
            # Track pop operations
            if transition["popped_symbol"] != "epsilon":  # If it's not epsilon, it's a pop
                if transition["popped_symbol"] not in stack_operations:
                    stack_operations[transition["popped_symbol"]] = {'pushed': 0, 'popped': 0}
                stack_operations[transition["popped_symbol"]]['popped'] += 1

    # Check if any pushed symbol was not popped
    for stack_symbol, operations in stack_operations.items():
        if operations['pushed'] > operations['popped']:
            error_message = f"Stack symbol '{stack_symbol}' was pushed but never fully popped. The stack needs to be emptied."
            print(error_message)
            raise ValueError(f"Stack not emptied: {error_message}. Please update the PDA input.")


def validate_stack_symbol_transitions(pda_json):
    """
    Check for transitions where the stack stays the same, which is invalid.
    """
    for current_state, transitions_list in pda_json["transitions"].items():
        for transition in transitions_list:
            # Check if both the push and pop operations are the same
            if transition["popped_symbol"] == transition["pushed_symbol"]:
                error_message = f"Popped symbol '{transition['popped_symbol']}' is the same as the pushed symbol '{transition['pushed_symbol']}' in transition from state '{current_state}' with input '{transition['input_symbol']}'"
                print(error_message)
                raise ValueError(f"PDA transitions incorrect: {error_message}. Please update the PDA input.")


def create_cfg_json(variables, alphabet, rules, start_variable):
    cfg = {
        "variables": variables,
        "alphabet": alphabet,
        "rules": rules,
        "start_variable": start_variable
    }
    return cfg


def find_push_to_pop(pda_json):
    pushed_popped_pairs = []
    seen_pairs = set()  # To track unique pairs

    # Iterate through each state and its transitions to identify push operations
    for start_state, transitions_list in pda_json["transitions"].items():
        for transition in transitions_list:
            push_symbol = transition["pushed_symbol"]
            end_state = transition["next_state"]
            
            # Check if it is a push operation (not epsilon)
            if push_symbol != "epsilon":
                # For each pushed symbol, look for its corresponding pops
                for pop_start_state, pop_transitions_list in pda_json["transitions"].items():
                    for pop_transition in pop_transitions_list:
                        pop_action_symbol = pop_transition["pushed_symbol"]
                        pop_check_symbol = pop_transition["popped_symbol"]
                        pop_end_state = pop_transition["next_state"]
                        
                        # Match pop if it is a pop of the same symbol with epsilon as the action
                        if pop_check_symbol == push_symbol and pop_action_symbol == "epsilon":
                            # Create a tuple to represent the unique pair
                            push_pop_pair_tuple = (
                                push_symbol,
                                start_state,
                                end_state,
                                pop_start_state,
                                pop_end_state
                            )
                            
                            # Add pair if it hasn't been seen
                            if push_pop_pair_tuple not in seen_pairs:
                                seen_pairs.add(push_pop_pair_tuple)
                                # Store as a dictionary for readability in results
                                push_pop_pair = {
                                    "stack_symbol": push_symbol,
                                    "start_push_state": start_state,
                                    "end_push_state": end_state,
                                    "start_pop_state": pop_start_state,
                                    "end_pop_state": pop_end_state
                                }
                                pushed_popped_pairs.append(push_pop_pair)

    # Print the found pairs for verification
    for pair in pushed_popped_pairs:
        print(f"Symbol: {pair['stack_symbol']}")
        print(f"Push: {pair['start_push_state']} -> {pair['end_push_state']}")
        print(f"Pop: {pair['start_pop_state']} -> {pair['end_pop_state']}")
        print()

    return pushed_popped_pairs


def generate_rules(pda_json, push_pop_pairs):
    # This will store the final rules
    rules = {}

    # Iterate through each push-pop pair
    for pair in push_pop_pairs:
        # Extract the necessary details from the pair
        push_symbol = pair['stack_symbol']
        start_push_state = pair['start_push_state']
        end_push_state = pair['end_push_state']
        start_pop_state = pair['start_pop_state']
        end_pop_state = pair['end_pop_state']

        # Find all matching input symbols for the push transition
        push_input_symbols = []
        for start_state, transitions_list in pda_json["transitions"].items():
            for transition in transitions_list:
                if transition["next_state"] == end_push_state and transition["pushed_symbol"] == push_symbol:
                    push_input_symbols.append(transition["input_symbol"])

        # Find all matching input symbols for the pop transition
        pop_input_symbols = []
        for start_state, transitions_list in pda_json["transitions"].items():
            for transition in transitions_list:
                if transition["next_state"] == end_pop_state and transition["popped_symbol"] == push_symbol:
                    pop_input_symbols.append(transition["input_symbol"])

        # Generate rules for all combinations of push and pop input symbols
        for push_input_symbol in push_input_symbols:
            for pop_input_symbol in pop_input_symbols:
                # Create the input rule (from push and pop state numbers)
                start_push_number = int(start_push_state[1:])  # Extracting the number from 'q1', 'q2', etc.
                end_pop_number = int(end_pop_state[1:])
                input_rule = f"A_{start_push_number}{end_pop_number}"

                # Create the output rule (using push and pop state numbers)
                end_push_number = int(end_push_state[1:])
                start_pop_number = int(start_pop_state[1:])
                output_rule = f"A_{end_push_number}{start_pop_number}"

                # Adjust the output rule based on the input symbols
                if pop_input_symbol == "epsilon" and push_input_symbol == "epsilon":
                    output_rule = f"epsilon {output_rule} epsilon"
                elif pop_input_symbol == "epsilon" and push_input_symbol is not None:
                    output_rule = f"{push_input_symbol} {output_rule} epsilon"
                elif pop_input_symbol is not None and push_input_symbol == "epsilon":
                    output_rule = f"epsilon {output_rule} {pop_input_symbol}"
                elif pop_input_symbol is not None and push_input_symbol is not None:
                    output_rule = f"{push_input_symbol} {output_rule} {pop_input_symbol}"

                # Append the rule to the list of rules for the input rule
                if input_rule in rules:
                    rules[input_rule] += f" | {output_rule}"
                else:
                    # Otherwise, create a new rule
                    rules[input_rule] = output_rule
    return rules


def finish_grammar(pda_json, rules):
    # Step 1: Remove unnecessary rules
    rules = prune_useless_rules(rules)
    
    # Step 2: Add A_ii -> epsilon rules for each i
    largest_transition_number = find_largest_transition_number(pda_json)
    add_epsilon_rules(rules, largest_transition_number)
    
    # Step 3: Add the final transition rule A_ik -> A_ij A_jk
    add_final_transition_rule(rules, largest_transition_number)

    # Return the modified rules
    return rules


def prune_useless_rules(rules):
    # Collect all the non-terminal symbols that are present on the left side of the rules (A_xx form)
    all_non_terminals = set(rules.keys())

    # Set to store the valid (useful) rules
    useful_rules = {}

    # Iterate over all the rules
    for input_rule, output_rule in rules.items():
        # Split the output rule into possible parts (if multiple options exist)
        parts = output_rule.split(" | ")
        
        # For each part, we check if it refers to a valid non-terminal or is of the A_ii form
        useful_parts = []
        for part in parts:
            # Split part by spaces, the second part should be the non-terminal if it exists
            split_part = part.strip().split()
            part_non_terminal = split_part[1] if len(split_part) > 1 else None
            number = int(part_non_terminal.strip().split("_")[1])
            
            # Check if the part is valid:
            # 1. It should either refer to an existing non-terminal (in all_non_terminals)
            # 2. Or be in the A_ii form (i.e., both numbers in A_xx are the same)
            if part_non_terminal:
                if part_non_terminal in all_non_terminals or part_non_terminal == split_part[0]:
                    useful_parts.append(part)
                elif number % 11 == 0:
                    useful_parts.append(part)

        # If there are any useful parts for this rule, we keep it
        if useful_parts:
            useful_rules[input_rule] = " | ".join(useful_parts)

    return useful_rules 


def find_largest_transition_number(pda_json):
    # Find the largest transition number from the PDA transitions
    max_number = 0
    for start_state, transitions_list in pda_json["transitions"].items():
        for transition in transitions_list:
            start_state_number = int(start_state[1:])  # Get the number from q1, q2, ...
            max_number = max(max_number, start_state_number)

            next_state_number = int(transition["next_state"][1:])
            max_number = max(max_number, next_state_number)

    return max_number


def add_epsilon_rules(rules, largest_transition_number):
    # Add A_ii -> epsilon rule for each i
    epsilon_rule = "A_ii"
    # Add the comment line for A_ii -> epsilon for 1 <= i <= max_number
    rules[epsilon_rule] = f"epsilon\n\tfor 1 <= i <= {largest_transition_number}"


def add_final_transition_rule(rules, largest_transition_number):
    # Add A_ik -> A_ij A_jk rule in general form
    final_rule = "A_ik"
    rules[final_rule] = f"A_ij A_jk\n\tfor 1 <= i <= {largest_transition_number}, 1 <= j <= {largest_transition_number}, 1 <= k <= {largest_transition_number}"


def print_grammar(grammar):
    for rule, rule_definition in grammar.items():
        print(f"{rule}:")
        # Split the definition into separate lines if necessary for readability
        formatted_definition = rule_definition.replace(" | ", " | ")
        print(f"\t{formatted_definition}")
        print()

def process_grammar_and_create_cfg(rules, pda_json):
    # Initialize sets for variables and alphabet
    variables = set()
    alphabet = set()

    # Extract variables and alphabet from the rules
    for key, value in rules.items():
        # Add the rule name (key) as a variable
        variables.add(key)
        
        # Parse the rule definitions
        parts = value.replace("\n", "").split(" | ")  # Split into individual rule components
        for part in parts:
            tokens = part.strip().split()
            for token in tokens:
                # Identify tokens that are variables or part of the alphabet
                if token.startswith("A_"):  # Variables are typically in the form A_xx
                    variables.add(token)

    # Order variables: numbered variables first, followed by letter variables
    def variable_order(var):
        if "_" in var:
            base, suffix = var.split("_")
            if suffix.isdigit():
                return (0, int(suffix))  # Prioritize numbered variables
            return (1, suffix)  # Followed by letter variables
        return (2, var)  # Handle any other cases if needed

    variables = sorted(variables, key=variable_order)

    alphabet = pda_json["input_symbols"]

    # The start variable is the first variable in the rule keys
    start_variable = next(iter(rules.keys()))

    # Call the create_cfg_json function
    cfg_json = create_cfg_json(variables, alphabet, rules, start_variable)
    return cfg_json


def write_cfg_to_csv(cfg, filename='output.csv'):
    with open(filename, mode='w', newline='') as file:
        # Write the header
        file.write("Component, Values\n")

        # Format and write variables
        variables = "{" + ", ".join(cfg["variables"]) + "}"
        file.write(f"Variables: {variables}\n")

        # Format and write alphabet
        alphabet = "{" + ", ".join(sorted(cfg["alphabet"], key=lambda x: (x.isdigit(), x))) + "}"
        file.write(f"Alphabet: {alphabet}\n")

        # Write rules
        file.write("Rules:\n")
        for lhs, rhs in cfg["rules"].items():
            file.write("\t")
            file.write(f"{lhs} -> ")
            rhs_lines = rhs.split("\n")  # Handle multiline rules
            for line in rhs_lines:
                if "for" in line:
                    # Indent "for" lines more deeply
                    file.write(f"\n\t\t{line.strip()}")
                else:
                    file.write(f"{line.strip()}")
            file.write("\n")
            

        # Write start variable
        file.write(f"Start Variable: {cfg["start_variable"]}")



# Convert CSV to JSON and print the result
pda_json = read_pda_from_csv('input.csv')
validate_pda(pda_json)
validate_pda_conversion(pda_json)
print("Here is the PDA:")
print(json.dumps(pda_json, indent=4))  # Pretty-print the JSON with indentation

# Get the push-pop pairs from the PDA
rules = find_push_to_pop(pda_json)

rules = generate_rules(pda_json, rules)
rules = finish_grammar(pda_json, rules)
print_grammar(rules)
cfg_json = process_grammar_and_create_cfg(rules, pda_json)
print(cfg_json)

# Write CFG JSON to CSV
write_cfg_to_csv(cfg_json)