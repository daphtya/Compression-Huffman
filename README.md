# Compression-Huffman
### Dibuat oleh David Timothy Panjaitan, NIM 13516075

Algoritma kompresi file menggunakan Huffman Coding Algorithm. Algoritma ini dipilih karena merupakan algoritma kompresi yang *lossless*, cukup sederhana, dan memiliki rasio kompresi yang cukup baik untuk beberapa jenis file.
Dibuat dengan bahasa Python versi 3.6.3.
Program utama ada pada main.py, sementara sebagian besar implementasi diletakkan pada compressed.py

## Penggunaan 

letakkan file yang ingin dikompresi pada folder yang sama, kemudian beri perintah melalui command line:
```
python main.py <NamaFile> 1
```
untuk kompresi file, yang akan menghasilkan file baru dengan extensi file diubah menjadi `.irk` dan:
```
python main.py <NamaFile> 2
```
untuk dekompresi file yang mengembalikan file ke bentuk semula. (file yang didekompresi menggunakan ekstensi `.irk`)

## Implemetasi
### 1. Kompresi
Pertama, program akan membaca per byte dari file yang diberikan pengguna. Dari bacaan pertama, program akan menghitung frekuensi kemunculan setiap byte dan menyimpannya dalam dictionary. Berdasarkan tabel frekuensi tersebut, dibuat pohon huffman. Pohon Huffman digunakan untuk memberi kode ke setiap byte sehingga kode terpendek diberikan untuk byte yang paling sering muncul dan seterusnya. Kemudian file dibaca sekali lagi. Daftar kode yang telah dihasilkan dalam bentuk dictionary digunakan untuk mengkodekan setiap byte dari file. Jumlah bit tidak terpakai dari byte terakhir (saya beri nama padding) juga disimpan untuk menghindari kesalahan saat pembacaan. Lalu, file baru dengan ekstensi `.irk` dibuat dan diisikan dengan ekstensi asli file, jumlah padding bit, pohon huffman dalam bentuk string of bytes, dan isi file yang telah dikodekan.

### 2. Dekompresi
Pertama, program membaca ekstensi file awal (sampai bertemu padding) dan jumlah padding (dalam 1 byte). Kemudian program membaca dan menerjemahkan byte-byte berikutnya sebagai pohon huffman dan diteruskan sampai terbentuk pohon biner komplit. Dari pohon yang dibentuk, program menentukan kode dan byte yang sesuai untuk mendekode file. Lalu, program melanjutkan pembacaan file dan mendekode file sampai byte terakhir file, dengan pengecualian bit padding di akhir. Hasil dekode disimpan dalam file baru dengan ekstensi `.irk` diganti ekstensi asli file.

## Analisis
### Kompleksitas
Dalam Kompresi, pembacaan  dan penghitungan frekuensisetiap byte pada file merupakan O(n) dengan n merupakan jumlah byte pada file. Akses kepada dictionary merupakan O(1) karena menggunakan fungsi hash. Pembuatan pohon huffman merupakan O(m^2) dengan m merupakan jumlah byte unik dalam suatu file (max: 256). Pembuatan daftar kode dari pohon Huffman memiliki kompleksitas O(m). Pengkodean file menggunakan kode yang telah dihasilkan merupakan O(n).

> Sehingga keseluruhan, kompleksitas dari algoritma kompresi adalah O(n + m^2)

Pada Dekompresi, pembacaan file merupakan O(n). Pembentukan Huffman tree dari string of byte merupakan O(m). Penggunaan pohon untuk membuat daftar kode untuk dekode juga merupakan O(m). Proses dekode sendiri dilakukan dengan pembacaan per bit sehingga sekitar 8 kali lebih banyak dari n, tapi kompleksitasnya tetap merupakan O(n).

> Sehingga keseluruhan, kompleksitas dari algoritma dekompresi adalah O(n + m)

### Kelebihan
Memori overhead yang dibutuhkan agar file dapat didekompresi relatif kecil. Karena hanya ada 256 variasi untuk 1 byte, secara teori, jumlah byte maksimal untuk mengkodekan pohon huffman di awal file adalah 320 byte (dengan 1 bit untuk menandai tiap simpul). Padding disimpan dalam 1 byte. Exstensi file yang umum memerlukan sekitar 3-4 byte. Selain itu, memori hanya digunakan untuk kode file.

### Kekurangan
Tidak efektif digunakan untuk mengkompresi file yang memiliki selisih frekuensi tidak terlalu besar antara byte paling sering dengan byte paling jarang. Selain itu, karena program hanya membaca per byte dan tidak mencari pola byte yang berulang, hasil kompresi mungkin tidak maksimal. Dalam beberapa kasus percobaan seperti mengkompresi file PNG, ukuran file hasil kompresi bahkan menjadi lebih besar dari file aslinya.