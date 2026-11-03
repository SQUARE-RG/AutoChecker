int main() {
    int value = 1;
    int* const const_ptr = &value;
    int* const* ptr_to_const_ptr = &const_ptr;
    int** mutable_ptr_ptr = const_cast<int**>(ptr_to_const_ptr); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    *mutable_ptr_ptr = &value;
    return 0;
}
