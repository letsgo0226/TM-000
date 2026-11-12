#!/usr/bin/env python3
"""G26: exact formal-log counterpart of G22/G23's ONE finite Turing machine.

The formal logarithm of the tape integer T is the finite coefficient vector
  Log(T) = sum_i exponent_i * [log(p_i)]
where basis elements [log(p_i)] are symbols, NOT floating-point logarithms.
Unique prime factorization gives exact equality, addition and subtraction.
No G24/G25 cross-domain applications, sources or external effects are present.
"""
from __future__ import annotations
import json
from G22_Blank_Tape_TM_core import (
    ALPHABET, create_self_printer, machine_from_canonical_code,
    encode_full_table, simulate, extract_output,
)
from G23_Prime_Power_TM_core import (
    zigzag, first_primes, exponent_at, prime_power_step, factor_tape,
    encode_configuration, decode_configuration, MAX_ABS_HEAD,
    MAX_SPARSE_CELLS,
)


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def formal_add(log_coeffs, position, delta):
    """Exact additive log operation: c_i <- c_i + delta in Z^(prime positions)."""
    require(type(position) is int and type(delta) is int, 'integer operands required')
    require(-8 <= delta <= 8, 'invalid symbol transition difference')
    result = dict(log_coeffs)
    old = result.get(position, 0)
    new = old + delta
    require(0 <= new < len(ALPHABET), 'invalid formal tape exponent')
    if new:
        result[position] = new
    else:
        result.pop(position, None)
    return result


def symbolic_log_product(coeff_a, coeff_b):
    """Formal log(XY)=log(X)+log(Y), including inverse rational powers."""
    c = dict(coeff_a)
    for position, exponent in coeff_b.items():
        require(type(position) is int and type(exponent) is int, 'integer log coefficients required')
        c[position] = c.get(position, 0) + exponent
        if c[position] == 0:
            del c[position]
    return c


def integer_from_formal(coeffs, primes):
    """Return a (possibly rational) exact encoded value as numerator, denominator."""
    up = down = 1
    for position, exponent in coeffs.items():
        require(type(position) is int and -MAX_ABS_HEAD <= position <= MAX_ABS_HEAD,
                'invalid position')
        require(type(exponent) is int and abs(exponent) <= 8, 'invalid log exponent')
        require(2 + zigzag(position) < len(primes), 'prime table too short')
        prime = primes[2 + zigzag(position)]
        if exponent > 0:
            up *= pow(prime, exponent)
        elif exponent < 0:
            down *= pow(prime, -exponent)
    return up, down


def run_g26(*, step_budget=4_000_000, strict_reads=4096, compare_g22=True):
    require(type(step_budget) is int and 1 <= step_budget <= 4_000_000,
            'invalid step budget')
    require(type(strict_reads) is int and 0 <= strict_reads <= step_budget,
            'invalid strict-read budget')
    machine, canonical = create_self_printer()
    primes = first_primes(2 * MAX_ABS_HEAD + 4)
    integer = 1
    tape = {}       # ordinary G22 cell semantics, value is symbol exponent
    log_coeffs = {}  # INDEPENDENT additive log ledger (not an alias of tape)
    head = 0
    state = 10
    steps = changes = inspected_reads = 0

    require(integer_from_formal(log_coeffs, primes) == (1, 1),
            'incorrect log 1 identity')
    while state != 9:
        require(steps < step_budget, 'STEP_LIMIT')
        require(-MAX_ABS_HEAD <= head <= MAX_ABS_HEAD, 'HEAD_BUDGET')
        old = tape.get(head, 0)
        prime = primes[2 + zigzag(head)]
        if steps < strict_reads:
            require(exponent_at(integer, prime) == old, 'inconsistent integer read')
            inspected_reads += 1
        instruction = machine.get((state, ALPHABET[old]))
        require(instruction is not None, 'STUCK')
        symbol, direction, state = instruction
        new = ALPHABET.index(symbol)
        if new != old:
            # G23: ACTUAL arbitrary-precision multiplication / exact division.
            integer = prime_power_step(integer, prime, old, new)
            # G26: exact additive formal log update, performed separately.
            log_coeffs = formal_add(log_coeffs, head, new - old)
            if new:
                tape[head] = new
            else:
                tape.pop(head, None)
            changes += 1
        head += (direction == 'R') - (direction == 'L')
        steps += 1
        require(len(tape) <= MAX_SPARSE_CELLS, 'CELL_BUDGET')

    decoded = factor_tape(integer, primes)  # independently factor ACTUAL bigint
    decoded_exponents = {i: ALPHABET.index(s) for i, s in decoded.items()}
    require(decoded_exponents == tape == log_coeffs,
            'G22 tape, G23 integer and G26 formal log do not agree')
    numerator, denominator = integer_from_formal(log_coeffs, primes)
    require(denominator == 1 and numerator == integer,
            'symbolic log exponential reconstruction failed')
    require(set(decoded) == set(range(len(canonical))), 'noncanonical output cells')
    final_bits = ''.join(decoded[i] for i in range(len(canonical)))
    require(final_bits == canonical, 'actual output differs from G22 full table code')
    require(machine_from_canonical_code(final_bits) == machine,
            'full rule table mismatch')
    require(encode_full_table(machine) == final_bits, 'full table codec drift')

    config_integer = encode_configuration(state, head, integer)
    require(decode_configuration(config_integer, primes) == (state, head, decoded),
            'G23 full configuration integer failed to decode')
    # The exact symbolic log of the full configuration has independent
    # reserved prime coefficients for state (2) and zigzag(head) (3).
    configuration_log = {2: state + 1, 3: zigzag(head) + 1}
    configuration_log.update({primes[2 + zigzag(i)]: exponent
                              for i, exponent in log_coeffs.items()})
    require(len(configuration_log) == len(log_coeffs) + 2,
            'reserved prime/log basis collision')
    if compare_g22:
        direct = simulate(machine, step_budget)
        require(direct['status'] == 'HALTED' and direct['steps'] == steps,
                'G22 transition count disagreement')
        require(extract_output(direct, len(canonical)) == final_bits,
                'G22 final tape discrepancy')

    return dict(
        version='G26', status='EXACT_FORMAL_LOG_G22_G23_TM_VERIFIED',
        original_rules=len(machine), steps=steps, prime_power_writes=changes,
        formal_log_additions=changes, integer_read_checks=inspected_reads,
        canonical_table_bits=len(final_bits), formal_log_terms=len(log_coeffs),
        tape_integer_bits=integer.bit_length(),
        full_configuration_integer_bits=config_integer.bit_length(),
        exact_log_addition=True, numerical_floating_logs_used=False,
        actual_prime_power_integer_updated=True,
        independent_full_integer_factorization=True,
        exact_log_integer_roundtrip=True, g22_output_equal=True,
        g23_prime_mapping_equal=True,
        full_configuration_log_symbols=len(configuration_log),
        paper_only=True, applications_integrated=False,
        future_g27_applications_integrated=False,
        sha_used=False, network_access=False, live_trades=0,
        autonomous_deployment=False, halting_oracle=False,
        literal_divinity_proved=False,
    )


if __name__ == '__main__':
    print(json.dumps(run_g26(), sort_keys=True))
