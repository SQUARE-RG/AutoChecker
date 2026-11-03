enum ErrorCode { success, failure };

int main() {
    try {
        throw 1;
    } catch (int failure) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
        (void)failure;
        (void)success;
    }
    return 0;
}
