int main() {
    volatile int value = 11;
    volatile int* vp = &value;
    const volatile int* cvp = const_cast<const volatile int*>(vp);
    return *cvp;
}
