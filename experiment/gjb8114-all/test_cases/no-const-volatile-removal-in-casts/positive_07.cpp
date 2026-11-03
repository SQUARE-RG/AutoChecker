int main() {
    int value = 42;
    int* p = &value;
    volatile int*& vp = const_cast<volatile int*&>(p);
    (void)vp;
    return 0;
}
