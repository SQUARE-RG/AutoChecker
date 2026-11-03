int main() {
    int errorCode = 0;
    try {
        throw errorCode;
    } catch (int CapturedErrorCode) {
        return CapturedErrorCode;
    }
    return 0;
}
