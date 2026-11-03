void set_handler(int id, void (*callback)(int));

int main() {
    set_handler(1, nullptr);
    return 0;
}

void set_handler(int id, void (*callback)(int)) {
    (void)id;
    (void)callback;
}
