int main() {
    int mode = 1;
    switch (mode) {
        case 1: {
            int selected = 0;
            ++selected;
            mode = selected;
            break;
        }
        default:
            break;
    }
    return mode;
}
