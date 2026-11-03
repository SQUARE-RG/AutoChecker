int main() {
    int value = 0;
    int* p = &value;
    decltype(&p) pp = nullptr;
    (void)pp;
    return 0;
}
