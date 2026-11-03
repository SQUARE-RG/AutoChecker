// positive_02.cpp
// 场景：通过 return 直接从嵌套循环返回，避免 goto。
int findPair(int target) {
    for (int i = 0; i < 10; ++i) {
        for (int j = 0; j < 10; ++j) {
            if (i * j == target) {
                return i * 10 + j;
            }
        }
    }
    return -1;
}

int main() {
    return findPair(12) >= 0 ? 0 : 1;
}
