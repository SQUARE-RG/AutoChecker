int computeTotal(int iBase) {
    static double elapsedSeconds; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-1]
    elapsedSeconds += 1.0;
    return iBase + static_cast<int>(elapsedSeconds);
}

int main() {
    return computeTotal(1);
}
