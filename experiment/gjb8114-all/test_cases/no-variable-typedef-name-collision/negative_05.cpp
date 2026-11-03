typedef long long Accumulator;
int main() {
    int total = 0;
    {
        long long Accumulator = 10; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
        total = static_cast<int>(Accumulator + 1);
    }
    return total;
}
