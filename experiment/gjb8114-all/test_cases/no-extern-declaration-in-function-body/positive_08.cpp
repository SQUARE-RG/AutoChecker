int shared_counter = 0;

template <typename T>
T read_shared_counter() {
    return shared_counter;
}

int main() {
    return read_shared_counter<int>();
}
