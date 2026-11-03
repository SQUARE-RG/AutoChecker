#include <vector>

int process_values(const std::vector<int>& values, int skip) {
    int total = 0;
    for (int value : values) {
        int remaining = value;
        while (remaining > 0) {
            if (remaining == skip) {
                --remaining;
                continue;
            }
            total += remaining;
            --remaining;
        }
    }
    return total;
}
