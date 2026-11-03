int main() {
    int state = 2;
    bool initialized = (state > 0) && (state < 10);
    return initialized ? 0 : 1;
}
