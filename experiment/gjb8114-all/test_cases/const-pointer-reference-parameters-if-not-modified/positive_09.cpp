template <typename T>
T read_first(const T* ptr) {
    return *ptr;
}

int main() {
    const int value = 7;
    return read_first(&value) == 7 ? 0 : 1;
}
