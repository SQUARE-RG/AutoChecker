// positive_05.cpp
int main() {
    int x = 2;
    int r = 0;
    switch (x) {
        case 1:
            r = 5;
            break;
        case 2:
            r = 7;
            goto after_switch;
        default:
            r = 9;
            break;
    }
after_switch:
    return r;
}
