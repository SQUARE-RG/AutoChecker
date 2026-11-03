int main() {
    int x = 0;
    goto after_block;
    {
        x = 1;
    }
    after_block:
    if (x == 0) {
        x = 2;
    }
    return x;
}
