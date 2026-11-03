int count_to_three() {
    int count = 0;
    int ticks = 0;
    while (1) {
        ++ticks;
        if (ticks < 3) {
            continue;
        }
        count = ticks;
        break;
    }
    return count;
}

int main() {
    return count_to_three() == 3 ? 0 : 1;
}
