int positive_05(int n) {
    int result = 0;
    while (true) {
        result += n;
        if (result > 100) {
            break;
        }
        if (n <= 0) {
            break;
        }
    }
    return result;
}
