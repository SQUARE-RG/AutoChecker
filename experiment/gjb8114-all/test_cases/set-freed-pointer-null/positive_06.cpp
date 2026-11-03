int main() {
    int mode = 0;
    int* p = new int(7);
    switch (mode) {
        case 0:
            delete p;
            p = nullptr;
            break;
        default:
            break;
    }
    return 0;
}
