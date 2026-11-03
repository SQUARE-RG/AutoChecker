// Static local variables that both contain 'l' and '1' but are clearly distinct.
int compute() {
    static int level1Total = 3;
    static int line1Count = 4;
    return level1Total + line1Count;
}

int main() {
    return compute();
}
