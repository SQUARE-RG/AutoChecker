// Positive: dynamically allocated single object is released before return.

int main() {
    int* value = new int(42);
    int result = *value;
    delete value;
    return result;
}
