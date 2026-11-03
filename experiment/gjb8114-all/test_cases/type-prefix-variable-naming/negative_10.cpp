int main() {
    int iNumbers[3] = {1, 2, 3};
    int iSum = 0;
    for (int value : iNumbers) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-1]
        iSum += value;
    }
    return iSum;
}
