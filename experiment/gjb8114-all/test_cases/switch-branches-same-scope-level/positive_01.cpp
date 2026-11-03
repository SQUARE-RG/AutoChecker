int main() {
    int x = 2;
    int result = 0;
    switch (x) {
        case 1:
            result = 10;
            break;
        case 2:
            if (x == 2) {
                result = 20;
            }
            break;
        default:
            result = 30;
            break;
    }
    return result;
}
