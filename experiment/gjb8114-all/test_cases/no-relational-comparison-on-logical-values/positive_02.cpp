int main() {
    bool a = true;
    bool b = false;
    if (a == b) {
        return 1;
    }
    bool c = a || b;
    if (c != false) {
        return 2;
    }
    return 0;
}
