bool has_value(const int* ptr) {
    return nullptr != ptr;
}

int main() {
    int value = 0;
    return has_value(&value) ? 0 : 1;
}
