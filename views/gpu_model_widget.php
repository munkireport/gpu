	<div class="col-lg-4 col-md-6">
	<div class="card" id="gpu-models-widget">
		<div class="card-header" data-container="body" >
			<i class="fa fa-desktop"></i>
			    <span data-i18n="gpu.widgettitle"></span>
			    <a href="/show/listing/gpu/gpu" class="pull-right"><i class="fa fa-list"></i></a>
			
		</div>
		<div class="list-group scroll-box"></div>
	</div><!-- /panel -->
</div><!-- /col -->

<script>
$(document).on('appUpdate', function(e, lang) {
	
	var box = $('#gpu-models-widget div.scroll-box');
	
	$.getJSON( appUrl + '/module/gpu/get_gpu_models', function( data ) {
		
		box.empty();
		if(data.length){
			$.each(data, function(i,d){
				var badge = '<span class="badge pull-right">'+d.count+'</span>';
                box.append('<a href="'+appUrl+'/show/listing/gpu/gpu/#'+d.model+'" class="list-group-item">'+d.model+badge+'</a>')
			});
		}
		else{
			box.append('<span class="list-group-item">'+i18n.t('gpu.nogpu')+'</span>');
		}
	});
});	
</script>
