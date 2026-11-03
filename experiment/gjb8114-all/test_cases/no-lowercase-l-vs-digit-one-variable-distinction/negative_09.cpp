// Static local variables whose names differ only by lowercase 'l' vs digit '1'.
int compute() {
    static int runCountl = 3;
    static int runCount1 = 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-9]
    return runCountl + runCount1;
}

int main() {
    return compute();
}
