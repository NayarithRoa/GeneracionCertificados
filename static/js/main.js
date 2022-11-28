const getTitleMessageFromCategory= category => {
    const titles= {
        'success':'Bien hecho!',
        'warning': 'Atención!',
        'info': 'Atención!',
        'error': 'Error!'
    }
}
function showMessageAlert(category, mensaje){
    Swal.fire({
        icon: category,
        title: '',
        text: mensaje
    })
}