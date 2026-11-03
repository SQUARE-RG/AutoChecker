int main() {
    int x = 1;
    switch (x) {
    case 0:
        x = 2;
        goto next;
    case 1:
    next:
        x = 3;
        break;
    default:
        break;
    }
    return 0;
}
