int main() {
    int value = 7;
    int* p = &value;
    volatile int* vp = const_cast<volatile int*>(p);
    *vp = 8;
    return value;
}
