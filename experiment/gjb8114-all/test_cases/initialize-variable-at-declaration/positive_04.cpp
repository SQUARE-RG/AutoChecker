#include <string>

int compute() { return 42; }

int main() {
    int value = compute();
    std::string label{"ready"};
    return (value == 42 && label == "ready") ? 0 : 1;
}
