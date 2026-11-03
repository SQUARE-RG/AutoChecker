int main() {
    int value = 0;
    auto gather = [&value]() {
        while (1) {
            ++value;
            if (value == 3) {
                break;
            }
        }
    };
    gather();
    return value == 3 ? 0 : 1;
}
