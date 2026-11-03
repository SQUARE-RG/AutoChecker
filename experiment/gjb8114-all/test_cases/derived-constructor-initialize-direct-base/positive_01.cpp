#include <iostream>

class Document {
public:
    Document() : docid(0) {}
    explicit Document(int value) : docid(value) {}
    int docid;
};

class Book : public Document {
public:
    int bookid;
    Book() : Document(1), bookid(1)
    {}
};

int main() {
    Book mybook;
    std::cout << mybook.bookid << mybook.docid << '\n';
    return 0;
}
