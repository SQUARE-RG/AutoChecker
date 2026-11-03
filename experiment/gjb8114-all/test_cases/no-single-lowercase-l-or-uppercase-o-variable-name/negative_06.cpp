int main() {
    auto addOne = [](int O) -> int { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-11]
        int number = O + 1;
        return number;
    };
    return addOne(1);
}
