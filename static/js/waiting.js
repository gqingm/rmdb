function createDialog(id, title, description) {
	$('<div id="'+id+'" align="center"></div>').html(description).dialog({
        title: title,
        autoOpen: false,
        modal: true,
        closeOnEscape: true,
        resizable: false,
        width: 400,
		buttons: {
			"Ok": function() {
				$( this ).dialog( "close" );
			}
		},
		create: function(event, ui) { 
		    var widget = $(this).dialog("widget");
		    $(".ui-dialog-titlebar-close", widget).append("<span class=\"ui-icon ui-icon-closethick\"></span>");
		    $("div.ui-dialog-buttonset button", widget).addClass("btn btn-primary btn-sm");
		},    
		open: function( event, ui ) {
			//this fixes the overlay of the dialog which does not fill the whole screen
			$(".ui-widget-overlay").css('position','fixed');
		}
    });
	
};


function setupWaitingCursorWithDescription(id, title, description) {
	$('<div id="'+id+'" align="center"></div>').html(description+'<br/><img src="/ecut/assets/images/ecut/wait.gif"/>').dialog({
        title: title,
        autoOpen: false,
        modal: true,
        closeOnEscape: false,
        resizable: false,
        width: 200,
        open: function(event, ui) { 
        	$(".ui-dialog-titlebar-close").hide();
        	//this fixes the overlay of the dialog which does not fill the whole screen
        	$(".ui-widget-overlay").css('position','fixed');
        },
        close: function(event, ui) { $(".ui-dialog-titlebar-close").show();}
    });
	
};

function setupWaitingCursorAtElement(id, title, description, element) {
	$('<div id="'+id+'" align="center"></div>').html(description+'<br/><img src="/ecut/assets/images/ecut/wait.gif"/>').dialog({
        title: title,
        autoOpen: false,
        modal: true,
        closeOnEscape: false,
        resizable: false,
        width: 200,
        position: { my: "center", at: "center", of: element },
        open: function(event, ui) { 
        	$(".ui-dialog-titlebar-close").hide();
        	//this fixes the overlay of the dialog which does not fill the whole screen
        	$(".ui-widget-overlay").css('position','fixed');
        },
        close: function(event, ui) { $(".ui-dialog-titlebar-close").show();}
    });
	
};


function setupWaitingCursor(id, title) {
	setupWaitingCursorWithDescription(id,title,"");
};

function attachWaitingCursorToAjax(id) {
	
	$(document).ajaxStart(function() {
		$("#"+id).dialog( 'open' );
		});
	$(document).ajaxStop(function() {
		$("#"+id).dialog( 'close' );
		});	
}

