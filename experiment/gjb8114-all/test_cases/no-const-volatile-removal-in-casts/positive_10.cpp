int main() {
    int value = 6;
    int* ptr = &value;
    int** ptr_ptr = &ptr;
    int* volatile* volatile_ptr_ptr = const_cast<int* volatile*>(ptr_ptr);
    (void)volatile_ptr_ptr;
    return 0;
}
