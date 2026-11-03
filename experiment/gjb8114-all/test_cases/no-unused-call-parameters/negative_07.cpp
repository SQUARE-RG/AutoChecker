int main() {
    struct Local {
        int compute(int value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-2]
            return 0;
        }
    };

    Local local;
    return local.compute(42);
}
