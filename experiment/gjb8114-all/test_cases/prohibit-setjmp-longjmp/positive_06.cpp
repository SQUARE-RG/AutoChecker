enum class State { ok, recovered };

State classify_state(int code) {
    switch (code) {
        case 0:
            return State::ok;
        default:
            return State::recovered;
    }
}

int main() {
    State s = classify_state(0);
    if (s == State::ok) {
        return 0;
    }
    return 1;
}
