int main() {
    bool outReg1 = true;
    bool outReg2 = false;
    if (outReg1 && !outReg2) {
        return 1;
    }
    if (!outReg1 && outReg2) {
        return 2;
    }
    return 0;
}
