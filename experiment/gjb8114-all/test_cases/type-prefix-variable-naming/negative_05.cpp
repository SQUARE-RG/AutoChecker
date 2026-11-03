// negative_05.cpp
// Intent: const-qualified local long variable is missing the l type prefix.
long compute(long lBase) {
    const long maxRetries = 3; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-1]
    return lBase + maxRetries;
}

int main() {
    return static_cast<int>(compute(4));
}
