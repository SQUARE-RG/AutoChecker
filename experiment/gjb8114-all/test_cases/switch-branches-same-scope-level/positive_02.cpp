int main() {
    int x = 1;
    int result = 0;
    switch (x) {
        case 0: {
            int temp = 100;
            result = temp;
            break;
        }
        case 1: {
            result = 200;
            break;
        }
        default: {
            result = 300;
            break;
        }
    }
    return result;
}
