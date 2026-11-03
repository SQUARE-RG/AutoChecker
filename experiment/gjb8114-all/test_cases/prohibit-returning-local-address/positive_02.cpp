int* create_dynamic_value() {
    return new int(5);
}

int main() {
    int* p = create_dynamic_value();
    delete p;
    return 0;
}
