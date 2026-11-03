#include <algorithm>
#include <vector>

int main() {
    std::vector<bool> flags{true, false, true};
    bool allTrue = std::all_of(flags.begin(), flags.end(), [](bool value) {
        return value;
    });
    return allTrue ? 0 : 1;
}
