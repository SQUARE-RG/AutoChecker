int main() {
    int value = 5;
    int* ptr = &value;
    int** ptr_ptr = &ptr;
    const int** const_ptr_ptr = const_cast<const int**>(ptr_ptr);
    (void)const_ptr_ptr;
    return 0;
}
