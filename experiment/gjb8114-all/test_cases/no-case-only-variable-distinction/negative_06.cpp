int main() {
    int errorCode = 0;
    try {
        throw errorCode;
    } catch (int ErrorCode) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]
        return ErrorCode;
    }
    return 0;
}
