#include <cmath>

int main() {
    double score = 73.6;
    long long rounded = std::llround(score);
    int finalScore = static_cast<int>(rounded);
    return finalScore == 74 ? 0 : 1;
}
