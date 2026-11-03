enum ErrorCode { success, failure };

int main() {
    try {
        throw 1;
    } catch (int error_code) {
        (void)error_code;
        int value = success;
        (void)value;
    }
    return 0;
}
