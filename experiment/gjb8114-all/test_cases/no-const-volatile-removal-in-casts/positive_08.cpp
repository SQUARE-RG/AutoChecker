int main() {
    int arr[3] = {1, 2, 3};
    volatile int (&vref)[3] = const_cast<volatile int (&)[3]>(arr);
    (void)vref;
    return 0;
}
